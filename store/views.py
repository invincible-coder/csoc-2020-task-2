from django.shortcuts import render
from django.shortcuts import get_object_or_404
from store.models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg

# Create your views here.

def index(request):
    return render(request, 'store/index.html')

def bookDetailView(request, bid):
    template_name = 'store/book_detail.html'
    try:
        book = Book.objects.get(pk=bid)
    except:
        return HttpResponse('<h1>Requested Book Not Available!</h1>')
    
    num_available = len(BookCopy.objects.filter(book__exact=book,status__exact=True))
    
    context = {
        'book': book, # set this to an instance of the required book
        'num_available': num_available, # set this to the number of copies of the book available, or 0 if the book isn't available
    }
    # START YOUR CODE HERE

    return render(request, template_name, context=context)


@csrf_exempt
def bookListView(request):
    template_name = 'store/book_list.html'
    get_data = request.GET

    books = Book.objects.filter(
        title__icontains=get_data.get('title',''), 
        author__icontains=get_data.get('author',''),
        genre__icontains=get_data.get('genre', '')
    )
    context = {
        'books': books, # set this to the list of required books upon filtering using the GET parameters
                       # (i.e. the book search feature will also be implemented in this view)
    }
    return render(request, template_name, context=context)

@login_required
def viewLoanedBooks(request):
    template_name = 'store/loaned_books.html'
    books = BookCopy.objects.filter(borrower__exact=request.user)
    context = {
        'books': books,
    }
    '''
    The above key 'books' in the context dictionary should contain a list of instances of the 
    BookCopy model. Only those book copies should be included which have been loaned by the user.
    '''
    # START YOUR CODE HERE
    


    return render(request, template_name, context=context)

@csrf_exempt
@login_required
def loanBookView(request):
    
    '''
    Check if an instance of the asked book is available.
    If yes, then set the message to 'success', otherwise 'failure'
    '''
    # START YOUR CODE HERE
    if not request.user.is_authenticated:
        return render(request,'login.html',{"message":"Login to loan book"})
    
    book_id = request.POST['bid']  # get the book id from post data
    books = BookCopy.objects.filter(book_id__exact=book_id, status__exact=True)
    if books:
            books[0].borrower = request.user
            books[0].borrow_date = datetime.date.today()
            books[0].status = False
            books[0].save()
            message = "success"
    else:
        message = "failure"
        response_data = {
            'message': message,
        }

    return JsonResponse(response_data)

'''
FILL IN THE BELOW VIEW BY YOURSELF.
This view will return the issued book.
You need to accept the book id as argument from a post request.
You additionally need to complete the returnBook function in the loaned_books.html file
to make this feature complete
''' 
@csrf_exempt
@login_required
def returnBookView(request):
    if request.method == "POST":
        try:
            book_id = request.POST['bid']
            book = BookCopy.objects.get(pk=book_id)
            book.borrower = None
            book.borrow_date = None
            book.status = True
            book.save()
            return JsonResponse( {"message":"Book returned successfully"} )
        except:
            return JsonResponse( {"message":"Book not found"} )
    else:
        return JsonResponse( {"message":"Invalid request method"} )

@csrf_exempt
@login_required
def rateBookView(request):
     if request.method == "POST":
         book_id = request.POST['bid']
         username = request.user.username
         new_rating = request.POST['rating']
         book = Book.objects.get(pk=book_id)

         if new_rating>10 or new_rating<0:
             return JsonResponse({'message':'Rating not in range 0-10'})
         else:
             try:
                 current_user_book_rating_object = BookRating.objects.get_or_create(book=book, username=username)
                 current_user_book_rating_object.rating = new_rating
                 current_user_book_rating_object.save()
                 
                 book.rating = BookRating.objects.filter(book = book).aggregate(rating=Avg('rating'))['rating']
                 book.save()                                                               
                 return JsonResponse({'message':'success'})
             except:
                 return JsonResponse({'message':"error"})

     else:
        return JsonResponse({'message':"Invalid request method"})
        
           
                 


